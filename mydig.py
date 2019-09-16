import dns.message
import dns.query
import dns.name
import datetime
import time
import sys


def main():
    start = time.time()  # just keep track of time

    website = sys.argv[1]
    webname = dns.name.from_text(website)
    if not webname.is_absolute():
        webname = webname.concatenate(dns.name.root)

    print("QUESTION SECTION:")
    print(website + " IN A\n")

    try:
        # keep querying starting at the root server and repeat until there is data in the ANSWER section
        message = dns.message.make_query(webname, dns.rdatatype.from_text('NS'))
        response = dns.query.udp(message, "199.7.91.13", 200)

        while len(response.answer) == 0:
            if (not len(response.authority) == 0) and (len(response.additional) == 0):
                ns = response.authority[0].to_text().split(' ')[4].split('\n')[0]
                # now find ip of ns
                temp = dns.message.make_query(ns, dns.rdatatype.from_text('A'))
                tresp = dns.query.udp(temp, "199.7.91.13", 200)
                while len(tresp.answer) == 0:
                    for findA in tresp.additional:
                        if findA.to_text().split(' ')[3] == 'A':  # if the ip is in A form, go ahead, otherwise skip it
                            add = findA.to_text().split(' ')[4].split('\n')[0]  # add now has the new ip to query to
                            tresp = dns.query.udp(temp, add, 200)
                            break
                # tresp now has an answer, aka an ip for temp
                ip = tresp.answer[0].to_text().split(' ')[4].split('\n')[0]
                response = dns.query.udp(message, ip, 200)

            else:
                # keep querying the dudes in the additional section
                # first parse the additional section
                for findA in response.additional:
                    if findA.to_text().split(' ')[3] == 'A':  # if the ip is in A form, go ahead, otherwise skip it
                        add = findA.to_text().split(' ')[4].split('\n')[0]  # add now has the new ip to query to
                        response = dns.query.udp(message, add, 200)
                        break

        # now there is something in answer
        # answer holds the website address of the auth name server
        # resolve that one now
        # auth name website to query for
        ans = response.answer[0].to_text().split(' ')[4].split('\n')[0]
        message2 = dns.message.make_query(ans, dns.rdatatype.from_text("A"))
        response2 = dns.query.udp(message2, "199.7.91.13", 200)
        while len(response2.answer) == 0:
            for findA in response2.additional:
                if findA.to_text().split(' ')[3] == 'A':  # if the ip is in A form, go ahead, otherwise skip it
                    add = findA.to_text().split(' ')[4].split('\n')[0]  # add now has the new ip to query to
                    response2 = dns.query.udp(message2, add, 200)
                    break

        # now response should have the ip address of the name server
        # we will query that ip with our original website
        auth = response2.answer[0].to_text().split(' ')[4].split('\n')[0]
        message3 = dns.message.make_query(website, dns.rdatatype.from_text("A"))  # now we do it with type A
        response3 = dns.query.udp(message3, auth, 200)

        # the answer section of response now holds all the ips
        print("ANSWER SECTION:")
        for answer in response3.answer:
            print(answer)
        print()

        # print query time
        in_sec = time.time() - start
        in_msec = int(in_sec * 1000)
        print("Query time: ", end='')
        print(in_msec, end='')
        print(" msec")

        # print current time
        date = datetime.datetime.now()
        print("WHEN: ", end='')
        print(date.strftime("%a %b %d %H:%M:%S %Y"))

        # print msg size
        print("MSG SIZE rcvd: ", end='')
        print(len(response.to_wire()))
    except dns.exception.Timeout:
        print("Timeout")


if __name__ == '__main__':
        main()